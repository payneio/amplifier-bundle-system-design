---
name: design-philosophy-object-oriented
description: "Object-oriented design principles as a lens for system architecture — SOLID, composition over inheritance, the actor model, design patterns (and when they're wrong), encapsulation, polymorphism, and responsibility-driven design. Use when evaluating code organization, module boundaries, or object/component relationships."
---

# Design Philosophy: Object-Oriented Design

OO principles as thinking tools for code organization, module boundaries, and component relationships.

---

## Core Premise

Object-oriented design is not about classes and inheritance. It is about **managing the cost of change** by localizing decisions behind stable interfaces. Every OO principle exists to answer one question: *when a requirement changes, how many places in the code must change with it?*

Good OO design means a single requirement change touches one or two files. Bad OO design means shotgun surgery across a class hierarchy that was supposed to make things "extensible."

The principles below are thinking tools, not commandments. Each one has a failure mode that is just as common as the problem it solves. Know both.

---

## 1. SOLID Principles

SOLID is a diagnostic framework. When code is hard to change, one of these principles usually explains why. But applying them prophylactically — before you feel the pain — produces the kind of over-abstracted architecture that makes senior engineers weep.

### S — Single Responsibility Principle

**The principle:** A class should have one reason to change. "Reason to change" means *one stakeholder* or *one axis of requirements evolution*.

**When it helps:**
- A class mixes persistence logic with business rules. The database schema changes, and you're editing the same file that implements pricing. Split them.
- A module handles both HTTP serialization and domain validation. These change for completely different reasons and at different rates.

**When it hurts:**
- Taken too far, SRP produces dozens of anemic classes that each do one trivial thing, connected by a web of delegation that nobody can follow. You've traded one 200-line class for fifteen 20-line classes and a wiring problem.
- The question is never "does this class do more than one thing?" — everything does more than one thing at some level of abstraction. The question is: **do these responsibilities change at the same time, for the same reasons?** If yes, they belong together. Cohesion matters more than smallness.

**The practical test:** Look at your git history. If a class changes in every commit for unrelated reasons, it has too many responsibilities. If you're always changing three classes together in lockstep, they may have been split incorrectly — they share a responsibility.

### O — Open/Closed Principle

**The principle:** Software entities should be open for extension but closed for modification. You should be able to add new behavior without editing existing, working code.

**When it helps:**
- You have a payment system and need to add new payment methods regularly. A strategy pattern or plugin architecture lets you add `StripePayment`, `PayPalPayment` without touching the payment processing core.
- Framework extension points: middleware chains, hook systems, event handlers. These are OCP applied well.

**When it hurts:**
- Premature openness. If you have one payment method and *might* add another someday, you don't need a `PaymentStrategy` interface with a factory and a registry. You need an `if` statement and the willingness to refactor later.
- Every extension point is a design commitment. It says "I expect variation here." If you're wrong about where variation will occur, you've added complexity at the wrong seams and the actual change still requires modification.

**The practical test:** You need OCP when you've added the third variant of something. The first is just code. The second might be an `if/else`. The third is when you extract the pattern. Not before.

### L — Liskov Substitution Principle

**The principle:** If `S` is a subtype of `T`, then objects of type `T` can be replaced with objects of type `S` without altering the correctness of the program. Subtypes must honor the behavioral contract of their parent, not just the type signature.

**When it helps:**
- API design. If your function accepts a `Stream`, every subclass of `Stream` must behave like a stream — same ordering guarantees, same error semantics. Callers should never need to check `isinstance` to decide how to use it.
- Type hierarchies in domain models. An `Employee` subclassing `Person` works if every operation valid on a `Person` is valid on an `Employee`. It breaks the moment `Person` has a method that doesn't apply to all subtypes.

**When it hurts:**
- The classic: `Square` inheriting from `Rectangle`. A square *is* a rectangle mathematically, but if `Rectangle` has independent `setWidth()` and `setHeight()`, `Square` cannot honor that contract without breaking its own invariant. The subtype relationship that seems obvious in the domain is *wrong* in code.
- This reveals the real lesson: **inheritance is a much stronger claim than most engineers realize.** It doesn't mean "shares some properties." It means "is fully substitutable in every context the parent appears." That's a hard contract to maintain as code evolves.

**The practical test:** Can you delete the type check? If code does `if isinstance(x, SpecificSubclass)` to handle a special case, LSP is violated. The subtype is not substitutable. Either fix the subtype's behavior or admit the hierarchy is wrong.

### I — Interface Segregation Principle

**The principle:** Clients should not be forced to depend on methods they do not use. Prefer many small, role-specific interfaces over one large general-purpose interface.

**When it helps:**
- A `Repository` interface with `find()`, `save()`, `delete()`, `bulkImport()`, `generateReport()`. Most clients only need `find()` and `save()`. The report generator only needs `find()`. Split into `Readable`, `Writable`, `BulkImportable` — each client depends on exactly what it uses.
- API surface area design. A module that exposes 40 public methods is hard to learn, hard to mock, and hard to evolve. Narrow interfaces let you change the implementation behind one role without affecting clients of another.

**When it hurts:**
- Interface explosion. If you create a separate interface for every single method, you've traded one comprehensibility problem for another. Group by role: "things a reader needs," "things a writer needs." Not by method count.
- In dynamic languages, ISP often happens naturally through duck typing. You don't need a formal `Readable` interface in Python — just document which methods your function actually calls.

**The practical test:** Look at your mocks in tests. If you're mocking 12 methods to test code that calls 2, your interface is too wide.

### D — Dependency Inversion Principle

**The principle:** High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details.

**When it helps:**
- Your business logic directly imports and calls `psycopg2`. Now you can't test it without a database, can't switch to a different store, and can't run it in a different context. Inverting the dependency — business logic defines a `Repository` interface, infrastructure provides the implementation — gives you testability and flexibility.
- Plugin systems. The host application defines interfaces; plugins implement them. The host never imports plugin code directly.

**When it hurts:**
- **You do not need an interface for everything.** If there is exactly one implementation of `UserRepository` and there will only ever be one, the interface is ceremony. The test can use the real thing or a simple fake.
- Dependency injection frameworks that require you to wire 47 bindings in a configuration file before your application starts. The cure is worse than the disease. Constructor injection with sensible defaults covers 90% of cases.
- DI becomes pathological when every class takes 8 interfaces in its constructor and you need a dependency graph visualizer to understand how the application boots.

**The practical test:** If adding a new feature requires editing a DI configuration file before writing any actual code, you've over-invested in inversion. If testing a class requires spinning up infrastructure, you've under-invested.

---

## 2. Composition Over Inheritance

**The principle:** Favor object composition (has-a) over class inheritance (is-a) for code reuse and flexibility.

### Why Inheritance Creates Brittleness

- **The fragile base class problem.** A change to a base class method can silently break subclasses that override related methods, or that depend on the base class's internal call sequence. The subclass author made assumptions about superclass behavior that aren't part of any explicit contract.
- **Inheritance couples the subclass to the superclass's implementation**, not just its interface. If the superclass changes how `save()` internally calls `validate()`, every subclass that overrides `validate()` might break.
- **Inheritance hierarchies are hard to change** once established. Inserting a new level, changing the root class, or refactoring the hierarchy breaks all descendants. Composition relationships can be rewired individually.
- **Multiple inheritance** makes all of these problems worse by introducing ambiguity (the diamond problem) and making the call chain unpredictable.

### Delegation as the Alternative

Instead of `class EnhancedList extends List`, create `class EnhancedList` that *contains* a `List` and forwards the methods it wants to expose. This is more code upfront but:
- You control exactly which methods are exposed (no accidental API surface).
- You can swap the inner implementation without affecting clients.
- You can compose multiple behaviors without a hierarchy.

### Mixins and Traits

Mixins (Python, Ruby) and traits (Rust, Scala) offer a middle path: reusable behavior chunks that don't create rigid hierarchies. They work well when:
- The behavior is genuinely orthogonal (serialization, logging, comparison).
- There's no shared mutable state between the mixin and the host class.
- The mixin doesn't depend on the host class's internal structure.

They go wrong when mixins start depending on each other's state, or when a class inherits from five mixins that all modify the same attributes.

### When Inheritance IS Appropriate

Inheritance is the right tool when:
- There is a genuine **behavioral** is-a relationship with a stable contract. A `TcpSocket` is a `Socket`. An `HttpError` is an `Error`. The superclass defines a behavioral contract that changes rarely.
- You're implementing the **template method** pattern: the superclass defines the algorithm skeleton, subclasses fill in the steps. This works when the algorithm structure is stable and the variation points are well-defined.
- Framework extension points explicitly designed for inheritance (Django views, JUnit test cases). The framework author has done the work to make the base class inheritance-safe.

Inheritance is the **wrong** tool when:
- You just want to reuse some methods. Use composition.
- The "is-a" relationship is about data shape, not behavior. A `PremiumUser` having all the fields of a `User` plus some extras is a composition relationship, not an inheritance relationship.
- You find yourself overriding superclass methods to disable them (returning `NotImplemented`, throwing `UnsupportedOperationException`). This is a Liskov violation — the hierarchy is wrong.

---

## 3. The Actor Model

### Core Concepts

The actor model treats **actors** as the fundamental unit of computation. Each actor:
- Has private state that no other actor can access directly.
- Communicates exclusively through asynchronous **message passing**.
- Processes one message at a time (no internal concurrency).
- Can create new actors, send messages, and decide how to handle the next message.

This eliminates shared mutable state by construction. There are no locks, no mutexes, no race conditions on shared data — because there is no shared data.

### Key Patterns

**Mailboxes.** Each actor has a message queue (mailbox). Messages arrive asynchronously and are processed sequentially. This gives you concurrency between actors and sequential consistency within each actor.

**Supervision trees** (Erlang/OTP, Akka). Actors are organized into hierarchies where parent actors supervise children. When a child fails, the supervisor decides: restart it, stop it, escalate. This turns "what do we do when something crashes" from an afterthought into an explicit architectural decision.

**Location transparency.** An actor reference doesn't encode whether the actor is in the same process, on another machine, or in another data center. Message passing works the same way regardless. This makes distribution an operational concern, not a code change.

**Behavior switching.** An actor can change its message-handling behavior in response to messages. This is a natural fit for state machines: an actor in the `authenticating` state handles messages differently than one in the `active` state.

### When Actors Are Right

- **Concurrent, stateful, isolated units.** A chat room that manages its participant list. A device controller that tracks hardware state. A shopping cart that accumulates items. Each of these is naturally an actor: private state, message-driven interaction, independent lifecycle.
- **Systems that need fault isolation.** One actor crashing should not bring down the system. Supervision trees make this explicit.
- **Distributed systems** where you need location transparency and message-based communication anyway.

### When Actors Are Overkill

- **Stateless request processing.** If your web handler reads a request, queries a database, and returns a response with no in-memory state between requests, actors add complexity with no benefit. Use a thread pool or async handlers.
- **Tight computational coupling.** If two components need to share a data structure and operate on it in tight loops, message-passing overhead is unacceptable. Use shared memory with proper synchronization.
- **Simple pub/sub.** If you just need "when X happens, notify Y," an event bus or observer pattern is simpler than a full actor system.
- **When you don't have the infrastructure.** Actor systems need good tooling for debugging, tracing, and monitoring. Without it, you're debugging distributed state machines with print statements.

---

## 4. Design Patterns — When They're Right and Wrong

The Gang of Four book is a **diagnostic tool**, not a cookbook. Each pattern is a named solution to a recurring design problem. If you don't have the problem, you don't need the pattern. Cargo-culting patterns because they sound sophisticated produces code that is harder to read, harder to debug, and harder to change — the exact opposite of what patterns are for.

### Creational Patterns

**Factory Method / Abstract Factory**

*The problem it solves:* The calling code shouldn't know which concrete class to instantiate. The decision depends on configuration, environment, or runtime state.

*The problem it creates:* Indirection. You're reading code that calls `createWidget()` and you have to chase through a factory hierarchy to find out what actually gets created. If there's only one implementation, the factory is a pointless layer.

*The simpler alternative:* A constructor. If you have one implementation, use `new Thing()` or just call the class directly. Extract a factory when you have the second implementation, not before.

*The signal you need it:* You're writing `if config == "postgres": return PostgresRepo() elif config == "mysql": return MysqlRepo()` in three different places. That's when a factory earns its keep.

**Builder**

*The problem it solves:* Constructing complex objects with many optional parameters. A constructor with 12 parameters is unreadable and error-prone.

*The problem it creates:* Builders are verbose. In languages with named parameters and default values (Python, Kotlin), a builder is often unnecessary ceremony.

*The simpler alternative:* Named parameters with defaults. A configuration dataclass. A builder is most valuable in languages without named parameters (Java, C++) or when construction requires multi-step validation.

**Singleton**

*The problem it solves:* Ensuring exactly one instance of a class exists and providing global access to it.

*The problem it creates:* Global state. Hidden dependencies. Testing nightmares (every test shares the same instance). Concurrency hazards. Singletons are the #1 pattern that engineers reach for and later regret.

*The simpler alternative:* Create one instance and pass it around. Dependency injection. Module-level instances (in Python, a module is already a singleton). If you truly need "only one," make that a deployment concern, not a code constraint.

*The rare case it's justified:* Hardware resources that genuinely have a single physical instance (the display, the GPU context). Even then, consider whether you can pass the reference explicitly.

### Structural Patterns

**Adapter**

*The problem it solves:* Making an existing class work with an interface it wasn't designed for. You have a `ThirdPartyLogger` but your code expects a `Logger` interface.

*The problem it creates:* An extra class that does almost nothing. If you own both sides, just change one of them.

*When it's right:* You don't own the adapted class (third-party library), or changing it would break other consumers. Adapters are legitimate anti-corruption layers.

**Facade**

*The problem it solves:* A complex subsystem with many interacting classes presents a simplified interface to the rest of the system.

*The problem it creates:* The facade can become a god object that everyone depends on. It can also become a leaky abstraction when callers need access to subsystem details the facade doesn't expose.

*When it's right:* Almost always. Facades are the most consistently useful structural pattern. Every well-designed module boundary is a facade. The key: make sure the facade represents a genuine abstraction, not just "all the methods of the subsystem dumped into one class."

**Decorator**

*The problem it solves:* Adding behavior to an object dynamically without modifying the class. `BufferedStream(CompressedStream(FileStream()))` — each layer adds behavior.

*The problem it creates:* Deep decorator chains become unreadable and hard to debug. When the `LoggingRepository(CachingRepository(RetryingRepository(ActualRepository())))` throws an error, good luck figuring out which layer is responsible. Stack traces become archaeological excavations.

*The simpler alternative:* For 1-2 behaviors, just put them in the class. Decorators earn their keep when the combinations are numerous and unpredictable (stream processing, middleware chains).

**Proxy**

*The problem it solves:* Controlling access to an object — lazy loading, access control, remote communication, caching.

*When it's right:* The caller genuinely shouldn't know about the control logic. A remote proxy that makes a network call look like a local call. A lazy proxy that defers expensive initialization.

*When it's wrong:* When the proxy is hiding important semantics. If calling `save()` on a proxy might fail because of a network error, the caller needs to know about that. Transparent proxies for inherently non-transparent operations are a lie.

### Behavioral Patterns

**Strategy**

*The problem it solves:* A family of algorithms that can be swapped at runtime. Sorting strategies, pricing strategies, routing strategies.

*The problem it creates:* If the strategies share significant state or have complex interactions with the context, you end up passing lots of data back and forth. The "clean separation" becomes a complex protocol.

*The simpler alternative:* A function parameter. In languages with first-class functions, `sort(items, key=lambda x: x.name)` is the strategy pattern without the class. You don't need `SortByNameStrategy implements SortStrategy`.

**Observer / Event System**

*The problem it solves:* When one object changes state, all its dependents are notified automatically. Decouples the thing that changes from the things that react.

*The problem it creates:* **Event soup.** With enough observers, understanding the system requires tracing event chains through multiple indirect callbacks. "When does the UI update?" becomes an investigation. Events triggering events triggering events creates unpredictable execution order and subtle bugs.

*The simpler alternative:* Direct method calls. If A always notifies B and C, just have A call B and C explicitly. Use Observer when the set of dependents is genuinely dynamic or unknown to the publisher.

*The discipline required:* Events should flow in one direction. If A observes B and B observes A, you have a cycle and you will have bugs. Event architectures need explicit flow direction.

**Command**

*The problem it solves:* Encapsulating a request as an object, enabling undo/redo, queuing, logging, and transaction-like semantics.

*When it's right:* You need undo. You need to queue operations. You need to serialize operations for replay. These are the three cases where Command earns its weight.

*When it's wrong:* Wrapping every method call in a command object "for flexibility." If you don't need undo, queuing, or replay, a command is just an indirect function call with extra classes.

**State Machine**

*The problem it solves:* Objects whose behavior depends on their state, with well-defined transitions between states.

*This pattern is chronically underused.* State machines make illegal states unrepresentable and invalid transitions impossible. An order that can be `PENDING -> PAID -> SHIPPED -> DELIVERED` or `PENDING -> CANCELLED` — with no other transitions allowed — is trivially correct as a state machine and a bug magnet as a bag of boolean flags.

*When it's right:* Any time you have a status field, you probably want a state machine. Any time you have code like `if status == 'active' and not cancelled and has_payment and not refunded`, you definitely want a state machine.

*The simpler alternative:* There often isn't one that's simpler AND correct. State machines are one of the few patterns that almost always justify their complexity.

---

## 5. Responsibility-Driven Design

### The Core Idea

Design objects by asking **"what is this object responsible for?"** — not "what data does this object contain?" Data-centric design (start with the schema, add methods to manipulate it) produces anemic domain models where the interesting logic lives in service classes that reach into objects and manipulate their fields. Responsibility-driven design produces objects that own their decisions.

### CRC Cards

**Class, Responsibility, Collaborators.** A design technique where you write on index cards:
- **Class name** — what is this thing?
- **Responsibilities** — what does it know? What does it do? (NOT what data it holds.)
- **Collaborators** — who does it work with to fulfill its responsibilities?

This is a thinking tool, not a formal methodology. The value is in forcing you to articulate *responsibilities* (behaviors, decisions) rather than *attributes* (fields, columns).

### Information Expert

**Assign a responsibility to the class that has the information needed to fulfill it.** If calculating the order total requires knowing the line items and their prices, the `Order` class should calculate the total — not an `OrderCalculatorService` that extracts data from the order and computes externally.

This sounds obvious, but the default instinct (especially in teams that use ORMs) is to treat domain objects as data containers and put all logic in stateless services. The result: objects that are just database rows with getters, and services that contain all the domain knowledge spread across hundreds of methods.

### The Controller Pattern

**A non-domain object that handles a system event and coordinates the response.** An HTTP handler, a message consumer, a CLI command handler. The controller's job is:
1. Receive the external event.
2. Translate it into domain operations.
3. Delegate to domain objects.
4. Return the result.

The controller should contain no business logic. If your controller has `if` statements about business rules, those rules belong in domain objects. The controller is a translator between the outside world and the domain model.

---

## 6. Encapsulation

### Information Hiding vs Data Hiding

These are often conflated but they're different:

- **Data hiding** means fields are private. This is the mechanical part — access modifiers, underscored attributes.
- **Information hiding** means the *design decisions* are hidden. Callers don't know how the object implements its behavior, what data structures it uses internally, or what algorithms it applies.

Data hiding without information hiding is useless. A class with a private field and a public getter/setter pair has hidden nothing — the internal representation is still part of the API. Change the field from an integer to a float and every caller breaks.

Information hiding is the real goal: **each component owns its decisions, and callers depend only on what the component does, not how it does it.**

### Tell, Don't Ask

Instead of:
```
if account.getBalance() >= amount:
    account.setBalance(account.getBalance() - amount)
```

Write:
```
account.withdraw(amount)
```

The first version asks for data, makes a decision, and pushes the result back. The logic for "can this withdrawal happen" lives in the caller. The second version tells the object what to do and lets it own the decision. The withdrawal rules (minimum balance, overdraft protection, daily limits) live where the data lives.

**Tell don't ask** means: give objects commands ("withdraw this amount," "ship this order," "approve this request"), not queries about their internal state followed by external decisions.

### The Law of Demeter

**A method should only call methods on:**
1. Its own object (`this` / `self`).
2. Its parameters.
3. Objects it creates.
4. Its direct component objects.

Not: `customer.getAddress().getCity().getZipCode()`. This chain couples the caller to the entire structure: Customer has an Address, Address has a City, City has a ZipCode. Change any link in that chain, and the caller breaks.

**When it goes too far:** Slavishly wrapping every access produces dozens of pass-through methods. `customer.getZipCode()` that just calls `address.getCity().getZipCode()` hasn't actually reduced coupling — it's hidden it behind a method that will still break if the structure changes.

The real question: **is the caller making a decision based on that deeply-nested data?** If yes, the decision should probably live closer to the data. If the caller is just passing the zip code along to some other function, a pass-through or a direct access is equally fine.

### Why Getter/Setter Pairs Break Encapsulation

A class with only getters and setters for every field is a struct with extra steps. It exposes its internal representation as its API. The "encapsulation" is an illusion:

- Any caller can depend on any field.
- Any caller can put the object into an invalid state by calling setters in the wrong order.
- Every field change is a breaking API change.

Better: expose **operations** (`deposit`, `transfer`, `close`) not **state** (`setBalance`, `setStatus`, `setClosed`). Let the object enforce its own invariants.

---

## 7. When OO Is Wrong

OO is a tool. It is a good tool for certain problems and a bad tool for others. The failure mode is not "OO is applied" but "OO is the only lens the team uses, so everything becomes a class hierarchy."

### Functional Transformations

Data pipelines — parse this, filter that, transform these, aggregate those — are naturally expressed as function composition. Wrapping each step in a class with a `process()` method adds indirection without adding value. `result = aggregate(transform(filter(parse(input))))` is clearer than a chain of `ProcessorStrategy` objects wired together by an `AbstractProcessorFactory`.

### Pure Data Transfer

DTOs (Data Transfer Objects) should not have behavior. They exist to carry data across boundaries — between services, between layers, across networks. Adding business logic to a DTO couples the transport format to the domain logic. A `UserDTO` with a `calculateAge()` method is a domain object pretending to be a data structure. Keep them separate.

### Data Flow Systems

Some systems are fundamentally about data flowing through transformations: ETL pipelines, compilers, signal processing chains. The natural model is functional: inputs, transformations, outputs. Trying to model these as object interactions (the `Compiler` sends a message to the `Parser` which creates `ASTNodes` which are visited by `Optimizers`) usually produces worse code than a pipeline of pure functions.

### Scripting and Glue Code

A 50-line script that reads a file, transforms some data, and writes the output doesn't need a class hierarchy. It needs functions. Possibly just one function. The overhead of defining classes, instantiating objects, and managing their lifecycle is not justified for code that runs once and is read twice.

### The Diagnostic

Ask: **Is the system fundamentally about independent entities with behavior and state that interact with each other?** If yes, OO is likely a good fit. If the system is fundamentally about transforming data from one shape to another, or about coordinating a sequence of steps, other paradigms will serve better.

---

## 8. Applying the Philosophy

### The Change Locality Test

The ultimate measure of OO design quality: **"If I change this requirement, how many files do I touch?"**

- **Good OO:** "We need to add a new discount type." You add one new class, register it in one place. Nothing else changes.
- **Bad OO:** "We need to add a new discount type." You modify the `Discount` base class, update the `DiscountFactory`, add a case to `DiscountValidator`, modify `DiscountSerializer`, update `DiscountController`, and change three test files.

If adding a new variant means touching every layer of the system, the class hierarchy is providing organization without providing isolation. You've paid the complexity tax of OO without getting the benefit.

### Refactoring Procedural Code Toward Good OO

**Step 1: Identify clusters.** Look for groups of functions that operate on the same data. Functions that always take the same first argument are methods waiting to be born.

**Step 2: Extract data classes.** Group related fields into objects. This is just data organization — no behavior yet.

**Step 3: Move behavior to data.** For each function that operates on a data class, ask: should this be a method? Apply the Information Expert pattern — if the function needs the object's data to make a decision, the decision belongs on the object.

**Step 4: Identify interfaces.** Where do you have switch statements or type-checking conditionals? Those are polymorphism waiting to happen. Extract an interface, create implementations.

**Step 5: Stop.** Not everything needs to be a class. Leave utility functions as functions. Leave scripts as scripts. Leave data as data. The goal is not "make everything OO." The goal is "put decisions next to the data they depend on, and hide those decisions behind stable interfaces."

### When to Stop Refactoring

You've gone far enough when:
- Each requirement change touches 1-3 files.
- You can explain what each class is *responsible for* in one sentence.
- You don't need to read the implementation to understand how to use the interface.
- Tests are easy to write without elaborate mocking.

You've gone too far when:
- You can't find where something happens without a dependency graph tool.
- Simple changes require modifying abstract base classes, interfaces, factories, and configuration.
- New team members need a week to understand the architecture.
- The abstraction layers outnumber the concrete implementations.

### The Final Heuristic

Good OO feels like the code already knows how to handle the change. You open the one file, make the one change, and everything else continues to work. Bad OO feels like you're negotiating with an architecture — convincing it to let you make a change it wasn't designed for, even though no design can anticipate every change. When the architecture is fighting you, it's wrong — regardless of how many patterns it uses.
