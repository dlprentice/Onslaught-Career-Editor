/* address: 0x004725d0 */
/* name: CExplosionInitThing__CheckValueRange_852_899 */
/* signature: int __fastcall CExplosionInitThing__CheckValueRange_852_899(int param_1) */


int __fastcall CExplosionInitThing__CheckValueRange_852_899(int param_1)

{
  if ((0x351 < *(int *)(param_1 + 0x2a0)) && (*(int *)(param_1 + 0x2a0) < 900)) {
    return 1;
  }
  return 0;
}
