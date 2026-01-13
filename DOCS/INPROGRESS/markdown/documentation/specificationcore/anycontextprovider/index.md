# AnyContextProvider

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AnyContextProvider
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A type-erased context provider.

## Discussion

### Overview

Use `AnyContextProvider` when you need to store heterogeneous `ContextProviding` instances in collections (e.g., for composition) or expose a stable provider type from APIs.

## Declarations
```swift
struct AnyContextProvider<Context>
```

## Topics

### Initializers
- init(_:)
- init(_:)

### Instance Methods
- currentContext()

### Default Implementations
- ContextProviding Implementations

## Relationships

### Conforms To
- ContextProviding
