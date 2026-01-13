# NotSpecification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/NotSpecification
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A specification that negates another specification.

## Discussion

### Overview

This specification is satisfied when the wrapped specification is NOT satisfied by the context, effectively inverting the boolean result.

### Example

```swift
let workingDaySpec = IsWorkingDaySpec()
let notWorkingDaySpec = NotSpecification(wrapped: workingDaySpec)

// Alternatively, use the convenience method:
let notWorkingDaySpec = workingDaySpec.not()
```

> **Note:** Prefer using the [not()](/documentation/specificationcore/specification/not()) method for better readability.

## Declarations
```swift
struct NotSpecification<Wrapped> where Wrapped : Specification
```

## Topics

### Instance Methods
- isSatisfiedBy(_:)

### Type Aliases
- NotSpecification.T

### Default Implementations
- Specification Implementations

## Relationships

### Conforms To
- Specification
