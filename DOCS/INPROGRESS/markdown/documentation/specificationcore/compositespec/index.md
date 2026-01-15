# CompositeSpec

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/CompositeSpec
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
An example composite specification that demonstrates how to combine multiple individual specifications into a single, reusable business rule. This serves as a template for creating domain-specific composite specifications.

## Declarations
```swift
struct CompositeSpec
```

## Topics

### Initializers
- init()
- init(minimumLaunchDelay:maxShowCount:cooldownDays:counterKey:eventKey:)

### Instance Methods
- isSatisfiedBy(_:)

### Type Aliases
- CompositeSpec.T

### Type Properties
- featureAnnouncement
- onboardingTip
- promoBanner
- ratingPrompt

### Default Implementations
- Specification Implementations

## Relationships

### Conforms To
- Specification
