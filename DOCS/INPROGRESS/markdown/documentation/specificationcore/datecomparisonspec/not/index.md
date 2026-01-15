# not()

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/DateComparisonSpec/not()
- **Module:** SpecificationCore
- **Symbol Kind:** method
- **Role Heading:** Instance Method
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
Creates a new specification that represents the logical NOT of this specification.

## Discussion

### Return Value

A new specification that is satisfied when this specification is not satisfied.

### Discussion

The resulting specification is satisfied when the current specification is NOT satisfied by the context.

### Example

```swift
let workingDaySpec = IsWorkingDaySpec()
let nonWorkingDaySpec = workingDaySpec.not()

let isOffDay = nonWorkingDaySpec.isSatisfiedBy(date)
// Returns true if date is NOT a working day
```

## Declarations
```swift
func not() -> NotSpecification<Self>
```
