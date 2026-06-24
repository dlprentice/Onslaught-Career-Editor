/* address: 0x00587daf */
/* name: CFastVB__Unk_00587daf */
/* signature: void __fastcall CFastVB__Unk_00587daf(void * param_1) */


void __fastcall CFastVB__Unk_00587daf(void *param_1)

{
  *(undefined ***)param_1 = &PTR_LAB_005ea138;
  CFastVB__Unk_00586bb7((int)param_1);
  if (*(void **)((int)param_1 + 0x1074) != (void *)0x0) {
    OID__FreeObject_Callback(*(void **)((int)param_1 + 0x1074));
  }
  CFastVB__Helper_00581263(param_1);
  return;
}
