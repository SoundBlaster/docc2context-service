# wrappedValue

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/Satisfies/wrappedValue
- **Module:** SpecificationCore
- **Symbol Kind:** property
- **Role Heading:** Instance Property
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
The wrapped value representing whether the specification is satisfied.

## Discussion

### Return Value

`true` if the specification is satisfied by the current context, `false` otherwise.

### Discussion

This property evaluates the specification against the current context each time it’s accessed, ensuring the result is always up-to-date.

## Declarations
```swift
var wrappedValue: Bool { get }
```
