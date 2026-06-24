/* address: 0x005989db */
/* name: CTexture__NodeType8_InitFromDescriptor */
/* signature: void __thiscall CTexture__NodeType8_InitFromDescriptor(void * this, void * param_1, void * param_2) */


void __thiscall CTexture__NodeType8_InitFromDescriptor(void *this,void *param_1,void *param_2)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 *)((int)this + 0xc) = 0;
  *(undefined4 *)((int)this + 4) = 2;
  *(undefined ***)this = &PTR_CFastVB__NodeType8_scalar_deleting_dtor_005ef240;
  puVar2 = (undefined4 *)((int)this + 0x10);
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = *(undefined4 *)param_1;
    param_1 = (undefined4 *)((int)param_1 + 4);
    puVar2 = puVar2 + 1;
  }
  return;
}
