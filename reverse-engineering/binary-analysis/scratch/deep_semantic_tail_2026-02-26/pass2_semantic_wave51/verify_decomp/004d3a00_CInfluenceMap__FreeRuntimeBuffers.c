/* address: 0x004d3a00 */
/* name: CInfluenceMap__FreeRuntimeBuffers */
/* signature: void __fastcall CInfluenceMap__FreeRuntimeBuffers(int param_1) */


void __fastcall CInfluenceMap__FreeRuntimeBuffers(int param_1)

{
  undefined4 *obj;
  void *obj_00;
  int iVar1;

  if (*(int *)(param_1 + 0x60) != 0) {
    if (*(int *)(param_1 + 0x7c) == 0) {
      iVar1 = 0;
      if (0 < *(int *)(param_1 + 0x68) * *(int *)(param_1 + 0x6c)) {
        do {
          obj = *(undefined4 **)(*(int *)(param_1 + 0x60) + iVar1 * 4);
          if (obj != (undefined4 *)0x0) {
            if (obj[3] == 0) {
              OID__FreeObject((void *)*obj);
            }
            OID__FreeObject(obj);
          }
          iVar1 = iVar1 + 1;
        } while (iVar1 < *(int *)(param_1 + 0x68) * *(int *)(param_1 + 0x6c));
      }
    }
    else {
      iVar1 = *(int *)(param_1 + 0x80);
      if (iVar1 != 0) {
        CDXLandscape__Helper_0055db0a(iVar1,0x10,*(int *)(iVar1 + -4),&LAB_004d3af0);
        OID__FreeObject((void *)(iVar1 + -4));
        *(undefined4 *)(param_1 + 0x80) = 0;
      }
      if (*(void **)(param_1 + 0x84) != (void *)0x0) {
        OID__FreeObject(*(void **)(param_1 + 0x84));
        *(undefined4 *)(param_1 + 0x84) = 0;
      }
    }
  }
  OID__FreeObject(*(void **)(param_1 + 0x60));
  OID__FreeObject(*(void **)(param_1 + 100));
  obj_00 = *(void **)(param_1 + 0x98);
  if (obj_00 != (void *)0x0) {
    CDXLandscape__Helper_005447d0(obj_00);
    OID__FreeObject(obj_00);
  }
  return;
}
