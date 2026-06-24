/* address: 0x00423870 */
/* name: CUnitAI__Unk_00423870 */
/* signature: void __thiscall CUnitAI__Unk_00423870(void * this, void * param_1, int param_2) */


void __thiscall CUnitAI__Unk_00423870(void *this,void *param_1,int param_2)

{
  void *obj;

  *(undefined4 *)this = 0;
  *(undefined4 *)((int)this + 8) = 0;
  if ((*(int *)((int)this + 0xc) != 0) && (obj = *(void **)((int)this + 4), obj != (void *)0x0)) {
    CChunker__Destructor();
    OID__FreeObject(obj);
    *(undefined4 *)((int)this + 4) = 0;
  }
  *(undefined4 *)((int)this + 0xc) = 0;
  *(void **)((int)this + 4) = param_1;
  return;
}
