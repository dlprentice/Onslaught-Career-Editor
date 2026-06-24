/* address: 0x00575923 */
/* name: CDXTexture__Helper_00575923 */
/* signature: int __stdcall CDXTexture__Helper_00575923(void * param_1, void * param_2) */


int CDXTexture__Helper_00575923(void *param_1,void *param_2)

{
  int iVar1;
  int extraout_EAX;
  void *extraout_EDX;
  void *extraout_EDX_00;
  void *pvVar2;
  int unaff_ESI;
  undefined1 local_14 [16];

  CDXTexture__InitMappedFileContext(local_14);
  iVar1 = CDXTexture__OpenMappedFileReadOnly(local_14,param_2,0,unaff_ESI);
  pvVar2 = extraout_EDX;
  if (-1 < iVar1) {
    CDXTexture__Helper_005758e6();
    iVar1 = extraout_EAX;
    pvVar2 = extraout_EDX_00;
  }
  CDXTexture__CloseHandleIfValid(local_14,pvVar2);
  return iVar1;
}
