# AutoContextSpecification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AutoContextSpecification
- **Module:** SpecificationCore
- **Symbol Kind:** protocol
- **Role Heading:** Protocol
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A protocol for specifications that can provide their own context.

## Discussion

### Overview

When a `Specification` conforms to this protocol, it can be used with the `@Satisfies` property wrapper without explicitly providing a context provider. The wrapper will use the `contextProvider` defined by the specification type itself.

## Declarations
```swift
protocol AutoContextSpecification : Specification
```

## Topics

### Associated Types
- Provider

### Initializers
- init()

### Type Properties
- contextProvider

## Relationships

### Inherits From
- Specification
