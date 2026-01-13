# OrSpecification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/OrSpecification
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A specification that combines two specifications with OR logic.

## Discussion

### Overview

This specification is satisfied when either the left or right specification (or both) are satisfied by the context. It provides short-circuit evaluation, meaning if the left specification succeeds, the right specification is not evaluated.

### Example

```swift
let weekendSpec = IsWeekendSpec()
let holidaySpec = IsHolidaySpec()
let combinedSpec = OrSpecification(left: weekendSpec, right: holidaySpec)

// Alternatively, use the convenience method:
let combinedSpec = weekendSpec.or(holidaySpec)
```

> **Note:** Prefer using the [or(_:)](/documentation/specificationcore/specification/or(_:)) method for better readability.

## Declarations
```swift
struct OrSpecification<Left, Right> where Left : Specification, Right : Specification, Left.T == Right.T
```

## Topics

### Instance Methods
- isSatisfiedBy(_:)

### Type Aliases
- OrSpecification.T

### Default Implementations
- Specification Implementations

## Relationships

### Conforms To
- Specification
