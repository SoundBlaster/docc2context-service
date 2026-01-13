# evaluate()

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AsyncSatisfies/Projection/evaluate()
- **Module:** SpecificationCore
- **Symbol Kind:** method
- **Role Heading:** Instance Method
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
Evaluates the specification asynchronously and returns the result.

## Discussion

### Return Value

`true` if the specification is satisfied, `false` otherwise

### Discussion

> **Note:** Any error that occurs during context fetching or specification evaluation

## Declarations
```swift
func evaluate() async throws -> Bool
```
