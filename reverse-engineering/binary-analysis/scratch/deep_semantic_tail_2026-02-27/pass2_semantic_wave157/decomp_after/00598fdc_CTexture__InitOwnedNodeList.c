/* address: 0x00598fdc */
/* name: CTexture__InitOwnedNodeList */
/* signature: void __thiscall CTexture__InitOwnedNodeList(void * this, void * param_1, int param_2) */


void __thiscall CTexture__InitOwnedNodeList(void *this,void *param_1,int param_2)

{
  *(undefined4 *)((int)this + 4) = 0;
  *(void **)this = param_1;
  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 **)((int)this + 0xc) = (undefined4 *)((int)this + 8);
  return;
}
