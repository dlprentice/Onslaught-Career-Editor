/* address: 0x0040dc90 */
/* name: CExplosionInitThing__CountFlag9CBySelectionMode */
/* signature: void __fastcall CExplosionInitThing__CountFlag9CBySelectionMode(int param_1) */


void __fastcall CExplosionInitThing__CountFlag9CBySelectionMode(int param_1)

{
  if (*(int *)(param_1 + 0x260) == 3) {
    LinkedObjectList__CountFlag9C(*(void **)(param_1 + 0x57c));
    return;
  }
  LinkedObjectList__CountFlag9C_IncludingExtra(*(void **)(param_1 + 0x578));
  return;
}
