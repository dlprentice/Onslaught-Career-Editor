/* address: 0x00527c90 */
/* name: CVBufTexture__Unk_00527c90 */
/* signature: int __thiscall CVBufTexture__Unk_00527c90(void * this, void * param_1, int param_2, int param_3) */


int __thiscall CVBufTexture__Unk_00527c90(void *this,void *param_1,int param_2,int param_3)

{
  int unaff_EDI;

  CTweak__ctor_like_00528690(this,param_1,unaff_EDI);
  *(void **)((int)this + 8) = param_1;
  *(undefined ***)this = &PTR_CReconnectInterface__VFunc_07_00527d00_005e4a80;
  *(int *)((int)this + 0xc) = param_2 + -1;
  *(undefined4 *)((int)this + 0x10) = 0;
  return (int)this;
}
