```
{
  otokens {
    tokenAddress
    underlying {
      id
      symbol
    }
    expiry
    strikePrice
  }
  underlyings {
    token {
      name
      symbol
    }
  }
  pools {
    lp
    locked
    size
    template {
      criteriaSet {
        criterias {
          id
        }
      }
    }
    snapshots {
      timestamp
      actionType
      actionAmount
    }
  }
}
```
