/* address: 0x0044c210 */
/* name: CUnitAI__Unk_0044c210 */
/* signature: void __thiscall CUnitAI__Unk_0044c210(void * this, void * param_1, int param_2) */


void __thiscall CUnitAI__Unk_0044c210(void *this,void *param_1,int param_2)

{
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)this = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 4) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 8) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x10) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x14) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x18) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x20) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x24) = param_1;
  DXMemBuffer__ReadBytes(&param_1,4);
  *(void **)((int)this + 0x28) = param_1;
  return;
}
