# BooleanDecisionAdapter

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/BooleanDecisionAdapter
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
An adapter that converts a boolean Specification into a DecisionSpec

## Declarations
```swift
struct BooleanDecisionAdapter<S, R> where S : Specification
```

## Topics

### Initializers
- init(specification:result:)

### Instance Methods
- decide(_:)

### Type Aliases
- BooleanDecisionAdapter.Context
- BooleanDecisionAdapter.Result

## Relationships

### Conforms To
- DecisionSpec
