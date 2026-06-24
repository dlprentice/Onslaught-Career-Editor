/* address: 0x00579cbe */
/* name: CDXTexture__Helper_00579cbe */
/* signature: void __fastcall CDXTexture__Helper_00579cbe(int param_1) */


void __fastcall CDXTexture__Helper_00579cbe(int param_1)

{
  void *pvVar1;

  if ((*(void **)(param_1 + 4) != (void *)0x0) && (*(int *)(param_1 + 0x38) != 0)) {
    OID__FreeObject_Callback(*(void **)(param_1 + 4));
  }
  if ((*(void **)(param_1 + 8) != (void *)0x0) && (*(int *)(param_1 + 0x3c) != 0)) {
    OID__FreeObject_Callback(*(void **)(param_1 + 8));
  }
  pvVar1 = *(void **)(param_1 + 0x4c);
  if (pvVar1 != (void *)0x0) {
    CDXTexture__Helper_00579cbe((int)pvVar1);
    OID__FreeObject_Callback(pvVar1);
  }
  pvVar1 = *(void **)(param_1 + 0x50);
  if (pvVar1 != (void *)0x0) {
    CDXTexture__Helper_00579cbe((int)pvVar1);
    OID__FreeObject_Callback(pvVar1);
  }
  return;
}
