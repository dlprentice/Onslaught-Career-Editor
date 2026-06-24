/* address: 0x004a17b0 */
/* name: CMemoryManager__UnlinkAndReleaseMutex */
/* signature: void __fastcall CMemoryManager__UnlinkAndReleaseMutex(void * param_1) */


void __fastcall CMemoryManager__UnlinkAndReleaseMutex(void *param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;

  piVar1 = DAT_009c3df0;
  piVar3 = (int *)0x0;
  if (DAT_009c3df0 != (int *)0x0) {
    do {
      piVar2 = piVar1;
      if (piVar2 == param_1) break;
      piVar1 = (int *)*piVar2;
      piVar3 = piVar2;
    } while ((int *)*piVar2 != (int *)0x0);
    if (piVar3 != (int *)0x0) {
      *piVar3 = *(int *)param_1;
      goto LAB_004a17dc;
    }
  }
  DAT_009c3df0 = *(int **)param_1;
LAB_004a17dc:
  CMeshCollisionVolume__Unk_0055f085(*(int *)((int)param_1 + 4));
  ReleaseMutex(*(HANDLE *)((int)param_1 + 0x8bc));
  *(undefined4 *)((int)param_1 + 0x8bc) = 0;
  return;
}
