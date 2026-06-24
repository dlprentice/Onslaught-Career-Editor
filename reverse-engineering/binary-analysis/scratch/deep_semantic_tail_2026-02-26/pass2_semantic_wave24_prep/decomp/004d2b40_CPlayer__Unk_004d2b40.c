/* address: 0x004d2b40 */
/* name: CPlayer__Unk_004d2b40 */
/* signature: void __thiscall CPlayer__Unk_004d2b40(void * this, int param_1, void * param_2) */


void __thiscall CPlayer__Unk_004d2b40(void *this,int param_1,void *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;

  local_10 = 0;
  local_c = 0;
  local_8 = 0;
  if (*(int **)(&DAT_008a9d58 + *(int *)((int)this + 0x2c) * 4) == (int *)0x0) {
    uVar2 = 0;
    uVar3 = 0;
    uVar4 = 0;
  }
  else {
    puVar1 = (undefined4 *)
             (**(code **)(**(int **)(&DAT_008a9d58 + *(int *)((int)this + 0x2c) * 4) + 8))
                       (&local_10);
    uVar4 = *puVar1;
    uVar3 = puVar1[1];
    uVar2 = puVar1[2];
    local_4 = puVar1[3];
  }
  *(undefined4 *)param_1 = uVar4;
  *(undefined4 *)(param_1 + 4) = uVar3;
  *(undefined4 *)(param_1 + 8) = uVar2;
  *(undefined4 *)(param_1 + 0xc) = local_4;
  return;
}
