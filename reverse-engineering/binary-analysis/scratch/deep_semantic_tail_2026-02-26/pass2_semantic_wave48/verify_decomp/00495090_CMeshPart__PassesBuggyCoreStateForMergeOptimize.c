/* address: 0x00495090 */
/* name: CMeshPart__PassesBuggyCoreStateForMergeOptimize */
/* signature: int __cdecl CMeshPart__PassesBuggyCoreStateForMergeOptimize(int param_1) */


int __cdecl CMeshPart__PassesBuggyCoreStateForMergeOptimize(int param_1)

{
  int iVar1;

  iVar1 = CMCBuggy__Helper_0056e170((void *)(param_1 + 0xdc),&DAT_0062896c,(void *)0x4);
  if (((iVar1 != 0) &&
      (iVar1 = CMCBuggy__Helper_0056e170((void *)(param_1 + 0xdc),&DAT_00628968,(void *)0x2),
      iVar1 != 0)) && (*(int *)(param_1 + 0xa0) < 1)) {
    if (*(int *)(param_1 + 0x8c) != 1) {
      return 1;
    }
    if (*(int *)(param_1 + 0xb0) < 0x15) {
      return 1;
    }
  }
  return 0;
}
