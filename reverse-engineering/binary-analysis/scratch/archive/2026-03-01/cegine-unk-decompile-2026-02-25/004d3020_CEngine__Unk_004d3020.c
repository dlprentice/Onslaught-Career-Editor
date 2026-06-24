/* address: 0x004d3020 */
/* name: CEngine__Unk_004d3020 */
/* signature: void __thiscall CEngine__Unk_004d3020(void * this, int param_1, float param_2) */


void __thiscall CEngine__Unk_004d3020(void *this,int param_1,float param_2)

{
  int iVar1;
  bool bVar2;

  *(int *)((int)this + 0x20) = param_1;
  (&CAREER_mMusicVolume)[*(int *)((int)this + 0x2c)] = (float)param_1;
  if (*(int **)((int)this + 0x1c) != (int *)0x0) {
    iVar1 = **(int **)((int)this + 0x1c);
    bVar2 = *(int *)((int)this + 0x20) != 1;
    if (bVar2) {
      (**(code **)(iVar1 + 0xe0))(1);
      iVar1 = **(int **)((int)this + 0x1c);
    }
    else {
      (**(code **)(iVar1 + 0xe0))(0);
      iVar1 = **(int **)((int)this + 0x1c);
    }
    (**(code **)(iVar1 + 0x154))(!bVar2);
  }
  if (param_1 != 0) {
    *(int *)((int)this + 0x3c) = *(int *)((int)this + 0x3c) + 1;
  }
  return;
}
