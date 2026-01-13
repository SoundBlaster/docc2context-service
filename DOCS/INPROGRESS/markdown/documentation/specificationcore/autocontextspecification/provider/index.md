# Provider

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AutoContextSpecification/Provider
- **Module:** SpecificationCore
- **Symbol Kind:** associatedtype
- **Role Heading:** Associated Type
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
The type of context provider this specification uses. The provider’s `Context` must match the specification’s associated type `T`.

## Declarations
```swift
associatedtype Provider : ContextProviding where Self.T == Self.Provider.Context
```
