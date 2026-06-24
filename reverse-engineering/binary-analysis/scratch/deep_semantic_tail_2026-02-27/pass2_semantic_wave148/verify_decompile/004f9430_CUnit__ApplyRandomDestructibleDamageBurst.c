/* address: 0x004f9430 */
/* name: CUnit__ApplyRandomDestructibleDamageBurst */
/* signature: void __fastcall CUnit__ApplyRandomDestructibleDamageBurst(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__ApplyRandomDestructibleDamageBurst(int param_1)

{
  uint uVar1;

  if (*(int *)(param_1 + 0x178) != 0) {
    CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold
              (*(int *)(param_1 + 0x178));
    return;
  }
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  *(float *)(param_1 + 0xf8) =
       *(float *)(param_1 + 0xf8) / ((float)(int)uVar1 * _DAT_005d8d4c + _DAT_005d8bd8);
  return;
}
