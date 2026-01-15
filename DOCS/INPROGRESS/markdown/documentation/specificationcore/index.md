# SpecificationCore

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Module:** SpecificationCore
- **Symbol Kind:** module
- **Role Heading:** Framework
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
Platform-independent core for building specification-based business logic in Swift.

## Discussion

### Overview

SpecificationCore provides the foundational protocols, specifications, property wrappers, and macros for implementing the Specification Pattern in Swift. It’s designed to be platform-independent and works across iOS, macOS, tvOS, watchOS, and Linux.

#### What is SpecificationCore?

SpecificationCore is the core library extracted from SpecificationKit that contains:

- Core protocols (`Specification`, `DecisionSpec`, `AsyncSpecification`)

- Context infrastructure (`EvaluationContext`, `DefaultContextProvider`)

- Basic specifications (`PredicateSpec`, `MaxCountSpec`, `FirstMatchSpec`, etc.)

- Property wrappers (`@Satisfies`, `@Decides`, `@Maybe`, `@AsyncSatisfies`)

- Swift macros (`@specs`, `@AutoContext`)

#### SpecificationCore vs SpecificationKit

- SpecificationCore: Platform-independent fundamentals. Use this for backend services, CLI tools, or when you don’t need platform-specific features.

- SpecificationKit: Builds on Core with SwiftUI integration, platform-specific context providers, and advanced specifications.

### Quick Start

#### Creating Your First Specification

```swift
import SpecificationCore

// Define a simple specification
struct PremiumUserSpec: Specification {
    func isSatisfiedBy(_ user: User) -> Bool {
        user.subscriptionTier == .premium && user.isActive
    }
}

// Use the specification
let spec = PremiumUserSpec()
let user = User(subscriptionTier: .premium, isActive: true)

if spec.isSatisfiedBy(user) {
    print("Premium user verified!")
}
```

#### Composing Specifications

```swift
// Combine specifications with logical operators
let eligibilitySpec = PremiumUserSpec()
    .and(MaxCountSpec(counterKey: "feature_used", maximumCount: 10))
    .and(TimeSinceEventSpec(eventKey: "last_usage", minimumInterval: 3600))

// Use with property wrapper
@Satisfies(using: eligibilitySpec)
var canUseFeature: Bool

if canUseFeature {
    performPremiumAction()
}
```

#### Working with Context

```swift
// Set up context
let provider = DefaultContextProvider.shared
provider.setCounter("feature_used", value: 5)
provider.recordEvent("last_usage")

// Specifications automatically use the context
@Satisfies(using: MaxCountSpec(counterKey: "feature_used", maximumCount: 10))
var hasUsesRemaining: Bool // true (5 < 10)
```

#### Decision Making

```swift
// Make decisions based on multiple specifications
@Decides([
    (PremiumUserSpec(), "premium_discount"),
    (FirstTimeUserSpec(), "welcome_discount"),
    (RegularUserSpec(), "standard_discount")
], or: "no_discount")
var discountType: String
```

## Topics

### Essentials
- Specification
- DecisionSpec
- AsyncSpecification
- ContextProviding

### Core Protocols
- Specification
- DecisionSpec
- AsyncSpecification
- ContextProviding
- AnySpecification
- AnyContextProvider

### Context Infrastructure
- EvaluationContext
- DefaultContextProvider
- MockContextProvider

### Basic Specifications
- PredicateSpec
- FirstMatchSpec
- MaxCountSpec
- CooldownIntervalSpec
- TimeSinceEventSpec
- DateRangeSpec
- DateComparisonSpec

### Property Wrappers
- Satisfies
- Decides
- Maybe
- AsyncSatisfies

### Macros
- @specs Macro
- @AutoContext Macro

### Composition and Operators
- Specification Operators and Builders

### Protocols
- AutoContextSpecification
- ContextUpdatesProviding

### Structures
- AdvancedCompositeSpec
- CompositeSpec
- ECommercePromoBannerSpec
- SatisfiesBuilder
- SubscriptionUpgradeSpec

### Functions
- build(_:)
- build(_:)
- contextProvider(_:)
- staticContext(_:)

### Type Aliases
- DecidesBuilder

### Extended Modules
- Swift
