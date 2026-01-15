# currentContextAsync()

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AnyContextProvider/currentContextAsync()
- **Module:** SpecificationCore
- **Symbol Kind:** method
- **Role Heading:** Instance Method
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
Async variant returning the current context. Default implementation bridges to sync.

## Discussion

### Return Value

A context instance containing the necessary data for evaluation

## Declarations
```swift
func currentContextAsync() async throws -> Context
```
