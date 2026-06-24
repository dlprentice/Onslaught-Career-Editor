/* address: 0x00536ca0 */
/* name: IScript__Unk_00536ca0 */
/* signature: void __thiscall IScript__Unk_00536ca0(void * this, int param_1, void * param_2) */


void __thiscall IScript__Unk_00536ca0(void *this,int param_1,void *param_2)

{
  float10 fVar1;

  if ((*(byte *)(*(int *)((int)this + 0x10) + 0x34) & 0x10) != 0) {
    fVar1 = (float10)(**(code **)(**(int **)param_1 + 0x34))();
    (**(code **)(**(int **)((int)this + 0x10) + 0x1ac))((float)fVar1);
  }
  return;
}
