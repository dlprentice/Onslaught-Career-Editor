/* address: 0x004443f0 */
/* name: CDestroyableSegment__Unk_004443f0 */
/* signature: void __fastcall CDestroyableSegment__Unk_004443f0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDestroyableSegment__Unk_004443f0(int param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int unaff_ESI;
  double dVar4;

  iVar3 = CDestroyableSegment__Unk_004433f0(*(int *)(param_1 + 0xc));
  if (iVar3 != 1) {
    fVar1 = *(float *)(param_1 + 0x18);
    fVar2 = (float)_DAT_005db0a0;
    dVar4 = CDestroyableSegment__Helper_00442890(*(void **)(param_1 + 0xc));
    if ((double)(fVar1 * fVar2) <= dVar4) {
      CDestructableSegment__SetSubtreeActiveFlagRecursive(*(int *)(param_1 + 0xc));
      CDestructableSegment__PropagateDamageToChildren
                (*(void **)(param_1 + 0xc),0x47c35000,unaff_ESI);
      *(undefined4 *)(param_1 + 0x2c) = 1;
    }
  }
  return;
}
