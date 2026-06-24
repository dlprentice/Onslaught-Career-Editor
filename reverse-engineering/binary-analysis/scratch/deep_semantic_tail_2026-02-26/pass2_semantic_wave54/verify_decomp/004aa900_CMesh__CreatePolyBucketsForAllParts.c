/* address: 0x004aa900 */
/* name: CMesh__CreatePolyBucketsForAllParts */
/* signature: void __fastcall CMesh__CreatePolyBucketsForAllParts(int param_1) */


void __fastcall CMesh__CreatePolyBucketsForAllParts(int param_1)

{
  int iVar1;

  if ((*(int *)(param_1 + 0x160) != 0) && (iVar1 = 0, 0 < *(int *)(param_1 + 0x15c))) {
    do {
      CMeshPart__CreatePolyBucket();
      iVar1 = iVar1 + 1;
    } while (iVar1 < *(int *)(param_1 + 0x15c));
  }
  return;
}
