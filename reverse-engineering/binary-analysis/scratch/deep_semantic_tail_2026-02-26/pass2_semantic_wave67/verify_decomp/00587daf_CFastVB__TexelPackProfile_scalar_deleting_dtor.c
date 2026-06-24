/* address: 0x00587daf */
/* name: CFastVB__TexelPackProfile_scalar_deleting_dtor */
/* signature: void __fastcall CFastVB__TexelPackProfile_scalar_deleting_dtor(void * param_1) */


void __fastcall CFastVB__TexelPackProfile_scalar_deleting_dtor(void *param_1)

{
  *(undefined ***)param_1 = &PTR_LAB_005ea138;
  CFastVB__FlushPendingConvertedRows16((int)param_1);
  if (*(void **)((int)param_1 + 0x1074) != (void *)0x0) {
    OID__FreeObject_Callback(*(void **)((int)param_1 + 0x1074));
  }
  CFastVB__Helper_00581263(param_1);
  return;
}
