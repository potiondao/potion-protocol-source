import { Bytes, BigDecimal, log } from "@graphprotocol/graph-ts";
import {
  CriteriaAdded,
  CriteriaSetAdded,
} from "../generated/CriteriaManager/CriteriaManager";
import {
  Criteria,
  CriteriaSet,
  CriteriaJoinedCriteriaSet,
} from "../generated/schema";
import { createTokenId } from "./token";

export function createCriteriaId(criteriaHash: Bytes): string {
  return criteriaHash.toHexString();
}

export function createCriteriaSetId(criteriaSetHash: Bytes): string {
  return criteriaSetHash.toHexString();
}

export function createCriteriaJoinedCriteriaSetId(
  criteriaHash: Bytes,
  criteriaSetHash: Bytes
): string {
  return criteriaHash.toHexString() + criteriaSetHash.toHexString();
}

/**
 * Called when a CriteriaAdded event is emitted. Creates a new criteria entity.
 * @param {CriteriaAdded} event Descriptor of the event emitted.
 */
export function handleCriteriaAdded(event: CriteriaAdded): void {
  const criteriaId = createCriteriaId(event.params.criteriaHash);
  let criteria = Criteria.load(criteriaId);
  if (criteria == null) {
    criteria = new Criteria(criteriaId);
    criteria.underlyingAsset = createTokenId(
      event.params.criteria.underlyingAsset
    );
    criteria.strikeAsset = createTokenId(event.params.criteria.strikeAsset);
    criteria.isPut = event.params.criteria.isPut;
    criteria.maxStrikePercent = BigDecimal.fromString(
      event.params.criteria.maxStrikePercent.toString()
    );
    criteria.maxDurationInDays = event.params.criteria.maxDurationInDays;
    criteria.save();
  } else {
    log.warning(
      "Tried to save the same criteria multiple times, criteriaId is {}",
      [criteriaId]
    );
  }
}

/**
 * Called when a CriteriaSetAdded event is emitted. Creates a new CriteriaSet entity.
 * @param {CriteriaSetAdded} event Descriptor of the event emitted.
 */
export function handleCriteriaSetAdded(event: CriteriaSetAdded): void {
  const criteriaSetId = event.params.criteriaSetHash;
  const criteriaSet = new CriteriaSet(criteriaSetId.toHexString());
  const criteriaHashArray = event.params.criteriaSet;

  for (let i = 0; i < criteriaHashArray.length; i++) {
    const criteriaHash: Bytes = criteriaHashArray[i];
    const criteriaId = createCriteriaId(criteriaHash as Bytes);
    const criteria = new Criteria(criteriaId);

    const criteriaJoinedCriteriaSetId = createCriteriaJoinedCriteriaSetId(
      criteriaHash as Bytes,
      event.params.criteriaSetHash
    );
    const criteriaJoinedCriteriaSet = new CriteriaJoinedCriteriaSet(
      criteriaJoinedCriteriaSetId
    );

    criteriaJoinedCriteriaSet.criteria = criteria.id;
    criteriaJoinedCriteriaSet.criteriaSet = criteriaSet.id;
    criteriaJoinedCriteriaSet.save();
  }

  criteriaSet.save();
}
