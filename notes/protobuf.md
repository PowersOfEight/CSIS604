# Protobuf

A small markdown based on notes taken from [the `protobuf` programming guide](https://protobuf.dev/programming-guides/proto3/)

---

## Defining A Message Type

Say we need to define a search request message, where the parameters include a query
string, a page, and a results per page.  In proto 3, this translates to

```proto
syntax = "proto3";

message SearchRequest {
  string query = 1;
  int32  page_number = 2;
  int32 results_per_page = 3;
}
```

Note that the first line specifying the `syntax` can be aliased to `edition`.  Also
note that the default for the _current_ compiler is `proto2`, so if neither is specified
that will be used.

## Field Typing

Here we define the `SearchRequest` message definition, specifying 3 fields (key-value pairs), one
for each parameter included in the message. Note that in addition to the **scalar types** such as
`int32` and `string`, one can also specify `enumerations` (enums) and composite types.

## Field Numbers

Each field in the message definition must be assigned a number between `1` and `536,870,911`.

* field numbers must be unique
* 19k -> 19,999 are reserved for the compiler.
* some field numbers may be allocated to extensions.  When this is the case, they may not be used
* Deleting/changing field number assignments once a message type is in use requires special caution

### Reserved Field Numbers

When updating or deleting(deprecating) fields, you may delete the field message from the message, **so long as you reserve the deleted field number**.
This is to maintain legacy consumers, and can be done in the following manner:

```proto
message Foo {
  reserved 1, 2, 3, 5, 8 to 11;
}
```

> [!NOTE]
> the `8 to 11` is inclusive, i.e. `8, 9, 10, 11`

Field names may also be reserved in the case of using TextProto or JSON encodings.

```proto
message Foo {
  reserved 1, 2, 3, 5, 8 to 11;
  reserved "foo", "bar";
}

```

## Field Cardinality

* Singular -> one of two types
  * `optional`: a field that may be set or unset. if unset, this field will return a default value
  * `implicit`: a field that has no explicit cardinality label (not recommended)
    * if the field is a message type, it behaves like an `optional` field
    * if the field is not a message type, it is set to the default value.
* `repeated`: can be repeated 0 or more times in a well-formed message.  the ordering of repeated values will be preserved.  these use `packed` encoding by default
* `map`: a key-value paired type

## Field Presence

_Field Presence_ is the notion of whether a protobuf field has a value.  

Message Type fields always have field presence, i.e. they always have a value.

Thus, in the example code below, `Message2` and `Message3` generate the same code
for all languages

```proto
syntax = "proto3"

package foo.bar;

message Message1 {}

message Message2 {
  Message1 foo = 1;
}

message Message3 {
  optional Message1 bar = 1;
}
```

## Multiple Message Types

```proto
syntax = "proto3"

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 results_per_page = 3;
}

message SearchResponse {
  //...
}
```

## Enumeration Type Example

```proto
enum Corpus {
  CORPUS_UNSPECIFIED = 0;
  CORPUS_UNIVERSAL = 1;
  CORPUS_WEB = 2;
  CORPUS_IMAGES = 3;
  CORPUS_LOCAL = 4;
  CORPUS_NEWS = 5;
  CORPUS_PRODUCTS = 6;
  CORPUS_VIDEO = 7;
}

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 results_per_page = 3;
  Corpus corpus = 4;
}
```

## Using Other Message Types

You may use other message types as a field

```proto
message SearchResponse {
  repeated Result results = 1;
}

message Result {
  string url = 1;
  string title = 2;
  repeated string snippets = 3;
}
```

## Importing Definitions

You can also import definitions from other files
