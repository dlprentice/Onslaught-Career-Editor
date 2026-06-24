/* address: 0x00598702 */
/* name: CTexture__NodePayloadBaseCtor */
/* signature: void __thiscall CTexture__NodePayloadBaseCtor(void * this, void * param_1, int param_2) */


void __thiscall CTexture__NodePayloadBaseCtor(void *this,void *param_1,int param_2)

{
  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 *)((int)this + 0xc) = 0;
  *(undefined ***)this = &PTR_CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag_005ef220;
  *(void **)((int)this + 4) = param_1;
  return;
}
