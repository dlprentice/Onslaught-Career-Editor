/* address: 0x004f6430 */
/* name: CTree__ComputeLodBucket */
/* signature: int __fastcall CTree__ComputeLodBucket(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CTree__ComputeLodBucket(int param_1)

{
  float fVar1;
  float fVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  int iVar6;
  byte bStack_8;

  iVar6 = (**(code **)(*(int *)(param_1 + 8) + 0x54))();
  fVar2 = *(float *)(iVar6 + 0x10);
  iVar6 = (**(code **)(*(int *)(param_1 + 8) + 0x54))();
  fVar1 = *(float *)(iVar6 + 0x14);
  bVar3 = NAN(fVar2);
  bVar4 = fVar1 < fVar2;
  bVar5 = fVar1 == fVar2;
  if (bVar4 == 0 && bVar5 == 0) {
    fVar2 = fVar1;
  }
  bStack_8 = (byte)(longlong)ROUND(fVar2 * _DAT_005d8be8);
  if (6 < bStack_8) {
    bStack_8 = 6;
  }
  return CONCAT31((int3)(CONCAT22((short)((uint)iVar6 >> 0x10),
                                  (ushort)bVar4 << 8 | (ushort)(NAN(fVar1) || bVar3) << 10 |
                                  (ushort)bVar5 << 0xe) >> 8),bStack_8);
}
