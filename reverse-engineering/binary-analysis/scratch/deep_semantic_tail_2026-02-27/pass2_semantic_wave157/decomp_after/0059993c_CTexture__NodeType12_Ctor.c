/* address: 0x0059993c */
/* name: CTexture__NodeType12_Ctor */
/* signature: int __fastcall CTexture__NodeType12_Ctor(void * param_1) */


int __fastcall CTexture__NodeType12_Ctor(void *param_1)

{
  int unaff_ESI;

  CTexture__Helper_00598702(param_1,(void *)0x12,unaff_ESI);
  *(undefined4 *)((int)param_1 + 0x10) = 0;
  *(undefined4 *)((int)param_1 + 0x14) = 0;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(undefined4 *)((int)param_1 + 0x28) = 0;
  *(undefined ***)param_1 = &PTR_CTexture__NodeType12_ScalarDeletingDtor_005ef384;
  *(undefined4 *)((int)param_1 + 0x20) = 0xf0000;
  *(undefined4 *)((int)param_1 + 0x24) = 0xe40000;
  return (int)param_1;
}
