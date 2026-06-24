/* address: 0x00580a00 */
/* name: CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate */
/* signature: int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(void * param_1) */


int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(void *param_1)

{
  int *piVar1;
  int iVar2;

  piVar1 = *(int **)((int)param_1 + 8);
  if ((piVar1 != (int *)0x0) || (piVar1 = *(int **)((int)param_1 + 4), piVar1 != (int *)0x0)) {
    (**(code **)(*piVar1 + 0x38))(piVar1);
  }
  if ((((*(int *)((int)param_1 + 4) != 0) && (*(int *)((int)param_1 + 8) != 0)) &&
      (*(int *)((int)param_1 + 0x10) != 0)) && ((*(byte *)param_1 & 1) == 0)) {
    CFastVB__Helper_00579bd5(1);
    iVar2 = (**(code **)(**(int **)((int)param_1 + 0x10) + 0x78))
                      (*(int **)((int)param_1 + 0x10),*(undefined4 *)((int)param_1 + 8),0,
                       *(undefined4 *)((int)param_1 + 4),0);
    CFastVB__Helper_00579bd5(0);
    if (iVar2 < 0) {
      CFastVB__Helper_00579bd5(1);
      CDXTexture__CopyLockedRectPitchAware
                (*(void **)((int)param_1 + 8),*(void **)((int)param_1 + 4));
      CFastVB__Helper_00579bd5(0);
    }
  }
  piVar1 = *(int **)((int)param_1 + 8);
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)((int)param_1 + 8) = 0;
  }
  piVar1 = *(int **)((int)param_1 + 0xc);
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)((int)param_1 + 0xc) = 0;
  }
  piVar1 = *(int **)((int)param_1 + 0x10);
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)((int)param_1 + 0x10) = 0;
  }
  piVar1 = *(int **)((int)param_1 + 4);
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)((int)param_1 + 4) = 0;
  }
  return 0;
}
