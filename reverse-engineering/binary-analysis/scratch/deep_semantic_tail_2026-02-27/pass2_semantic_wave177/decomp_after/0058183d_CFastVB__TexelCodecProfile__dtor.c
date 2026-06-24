/* address: 0x0058183d */
/* name: CFastVB__TexelCodecProfile__dtor */
/* signature: void __fastcall CFastVB__TexelCodecProfile__dtor(void * param_1) */


void __fastcall CFastVB__TexelCodecProfile__dtor(void *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;

  *(undefined ***)param_1 = &PTR_CFastVB__TexelCodecProfile_scalar_deleting_dtor_005e9ee4;
  if (((*(int *)((int)param_1 + 0x10e8) != 0) &&
      (iVar2 = *(int *)((int)param_1 + 0x10ec), iVar2 != 0)) &&
     (uVar3 = *(uint *)((int)param_1 + 0x10c8), uVar3 < *(uint *)((int)param_1 + 0x10cc))) {
    do {
      for (uVar1 = *(uint *)((int)param_1 + 0x10bc); uVar1 < *(uint *)((int)param_1 + 0x10c4);
          uVar1 = uVar1 + 4) {
        OID__FreeObject_Callback(*(void **)(iVar2 + 4));
        iVar2 = iVar2 + 8;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < *(uint *)((int)param_1 + 0x10cc));
  }
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0x10e4));
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0x10ec));
  CFastVB__TexelUnpackProfile__dtor(param_1);
  return;
}
