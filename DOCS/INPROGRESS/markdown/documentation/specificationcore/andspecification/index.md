# AndSpecification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AndSpecification
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A specification that combines two specifications with AND logic.

## Discussion

### Overview

This specification is satisfied only when both the left and right specifications are satisfied by the same context. It provides short-circuit evaluation, meaning if the left specification fails, the right specification is not evaluated.

### Example

```swift
let ageSpec = UserAgeSpec(minimumAge: 18)
let citizenshipSpec = UserCitizenshipSpec(country: .usa)
let combinedSpec = AndSpecification(left: ageSpec, right: citizenshipSpec)

// Alternatively, use the convenience method:
let combinedSpec = ageSpec.and(citizenshipSpec)
```

> **Note:** Prefer using the [and(_:)](/documentation/specificationcore/specification/and(_:)) method for better readability.

## Declarations
```swift
struct AndSpecification<Left, Right> where Left : Specification, Right : Specification, Left.T == Right.T
```

## Topics

### Instance Methods
- isSatisfiedBy(_:)

### Type Aliases
- AndSpecification.T

### Default Implementations
- Specification Implementations

## Relationships

### Conforms To
- Specification
