# Specification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/Specification
- **Module:** SpecificationCore
- **Symbol Kind:** protocol
- **Role Heading:** Protocol
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A specification that evaluates whether a context satisfies certain conditions.

## Discussion

### Overview

The `Specification` protocol is the foundation of the SpecificationCore framework, implementing the Specification Pattern to encapsulate business rules and conditions in a composable, testable manner.

### Overview

Specifications allow you to define complex business logic through small, focused components that can be combined using logical operators. This approach promotes code reusability, testability, and maintainability.

### Basic Usage

```swift
struct UserAgeSpec: Specification {
    let minimumAge: Int

    func isSatisfiedBy(_ user: User) -> Bool {
        return user.age >= minimumAge
    }
}

let adultSpec = UserAgeSpec(minimumAge: 18)
let canVote = adultSpec.isSatisfiedBy(user)
```

### Composition

Specifications can be combined using logical operators:

```swift
let adultSpec = UserAgeSpec(minimumAge: 18)
let citizenSpec = UserCitizenshipSpec(country: .usa)
let canVoteSpec = adultSpec.and(citizenSpec)
```

### Property Wrapper Integration

Use property wrappers for declarative specification evaluation:

```swift
struct Model {
    @Satisfies(using: adultSpec.and(citizenSpec))
    var canVote: Bool
}
```

## Declarations
```swift
protocol Specification<T>
```

## Topics

### Creating Specifications
- isSatisfiedBy(_:)

### Composition
- and(_:)
- or(_:)
- not()

### Built-in Specifications
- PredicateSpec
- CooldownIntervalSpec
- MaxCountSpec

### Essential Protocol
- isSatisfiedBy(_:)

### Logical Composition
- and(_:)
- or(_:)
- not()

### Composite Types
- AndSpecification
- OrSpecification
- NotSpecification

### Type Erasure
- AnySpecification

### Related Protocols
- DecisionSpec
- AsyncSpecification

### Built-in Specifications
- PredicateSpec
- MaxCountSpec
- CooldownIntervalSpec
- TimeSinceEventSpec
- DateRangeSpec
- DateComparisonSpec

### Property Wrappers
- Satisfies
- Decides
- Maybe

### Associated Types
- T

### Instance Methods
- returning(_:)

## Relationships

### Inherited By
- AutoContextSpecification

### Conforming Types
- AdvancedCompositeSpec
- AlwaysFalseSpec
- AlwaysTrueSpec
- AndSpecification
- AnySpecification
- CompositeSpec
- CooldownIntervalSpec
- DateComparisonSpec
- DateRangeSpec
- ECommercePromoBannerSpec
- MaxCountSpec
- NotSpecification
- OrSpecification
- PredicateSpec
- SubscriptionUpgradeSpec
- TimeSinceEventSpec
