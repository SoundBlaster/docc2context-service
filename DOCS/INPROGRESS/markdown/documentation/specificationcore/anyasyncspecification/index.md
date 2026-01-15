# AnyAsyncSpecification

## Symbol Metadata
- **Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore/AnyAsyncSpecification
- **Module:** SpecificationCore
- **Symbol Kind:** struct
- **Role Heading:** Structure
- **Catalog Identifier:** doc://specificationcore.SpecificationCore/documentation/SpecificationCore
- **Catalog Title:** SpecificationCore

## Summary
A type-erased wrapper for any asynchronous specification.

## Discussion

### Overview

`AnyAsyncSpecification` allows you to store async specifications of different concrete types in the same collection or use them in contexts where the specific type isn’t known at compile time. It also provides bridging from synchronous specifications to async context.

### Usage Examples

#### Type Erasure for Collections

```swift
let asyncSpecs: [AnyAsyncSpecification<EvaluationContext>] = [
    AnyAsyncSpecification(RemoteFeatureFlagSpec(flagKey: "feature_a")),
    AnyAsyncSpecification(DatabaseUserSpec()),
    AnyAsyncSpecification(MaxCountSpec(counterKey: "attempts", maximumCount: 3)) // sync spec
]

for spec in asyncSpecs {
    let result = try await spec.isSatisfiedBy(context)
    print("Spec satisfied: \(result)")
}
```

#### Bridging Synchronous Specifications

```swift
let syncSpec = MaxCountSpec(counterKey: "login_attempts", maximumCount: 3)
let asyncSpec = AnyAsyncSpecification(syncSpec) // Bridge to async

let isAllowed = try await asyncSpec.isSatisfiedBy(context)
```

#### Custom Async Logic

```swift
let customAsyncSpec = AnyAsyncSpecification<EvaluationContext> { context in
    // Simulate async network call
    try await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
    return context.flag(for: "delayed_feature") == true
}
```

## Declarations
```swift
struct AnyAsyncSpecification<T>
```

## Topics

### Initializers
- init(_:)
- init(_:)
- init(_:)

### Instance Methods
- isSatisfiedBy(_:)

## Relationships

### Conforms To
- AsyncSpecification
