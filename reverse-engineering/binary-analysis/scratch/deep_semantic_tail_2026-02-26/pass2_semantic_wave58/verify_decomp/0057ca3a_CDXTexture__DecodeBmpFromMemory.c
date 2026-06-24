/* address: 0x0057ca3a */
/* name: CDXTexture__DecodeBmpFromMemory */
/* signature: int __thiscall CDXTexture__DecodeBmpFromMemory(void * this, void * param_1, void * param_2, uint param_3) */


int __thiscall CDXTexture__DecodeBmpFromMemory(void *this,void *param_1,void *param_2,uint param_3)

{
  int iVar1;
  void *unaff_retaddr;

  if (((param_2 < (void *)0xe) || (*(short *)param_1 != 0x4d42)) ||
     (param_2 < *(void **)((int)param_1 + 2))) {
    iVar1 = -0x7fffbffb;
  }
  else {
    iVar1 = CDXTexture__Unk_00579e08
                      (this,(void *)((int)param_1 + 0xe),(void *)((int)param_2 + -0xe),unaff_retaddr
                      );
  }
  return iVar1;
}
