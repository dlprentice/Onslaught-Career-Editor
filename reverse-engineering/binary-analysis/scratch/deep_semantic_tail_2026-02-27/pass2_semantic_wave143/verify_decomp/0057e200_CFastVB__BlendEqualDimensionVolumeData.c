/* address: 0x0057e200 */
/* name: CFastVB__BlendEqualDimensionVolumeData */
/* signature: int __fastcall CFastVB__BlendEqualDimensionVolumeData(void * param_1) */


int __fastcall CFastVB__BlendEqualDimensionVolumeData(void *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  void *extraout_EAX;
  uint uVar4;
  uint uVar5;
  void *ptr;
  uint uVar6;

  iVar1 = *(int *)((int)param_1 + 4);
  iVar2 = *(int *)param_1;
  iVar3 = *(int *)(iVar1 + 0x1060);
  if (((iVar3 == *(int *)(iVar2 + 0x1060)) && (*(int *)(iVar1 + 0x1064) == *(int *)(iVar2 + 0x1064))
      ) && (*(int *)(iVar1 + 0x1068) == *(int *)(iVar2 + 0x1068))) {
    CFastVB__Helper_00426fd0(iVar3 << 4);
    uVar5 = 0;
    if (extraout_EAX == (void *)0x0) {
      ptr = (void *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar3,CFastVB__Helper_00574577);
      ptr = extraout_EAX;
    }
    if (ptr != (void *)0x0) {
      if ((*(int *)(*(int *)((int)param_1 + 4) + 0x10) != 0) &&
         (*(int *)(*(int *)param_1 + 0x10) != 0)) {
        *(undefined4 *)(*(int *)((int)param_1 + 4) + 0x10) = 0;
        *(undefined4 *)(*(int *)param_1 + 0x10) = 0;
      }
      if (*(int *)(*(int *)((int)param_1 + 4) + 0x1068) != 0) {
        uVar4 = *(uint *)(*(int *)((int)param_1 + 4) + 0x1064);
        do {
          uVar6 = 0;
          if (uVar4 != 0) {
            do {
              (**(code **)(**(int **)param_1 + 4))(uVar6,uVar5,ptr);
              (**(code **)(**(int **)((int)param_1 + 4) + 8))(uVar6,uVar5,ptr);
              uVar4 = *(uint *)(*(int *)((int)param_1 + 4) + 0x1064);
              uVar6 = uVar6 + 1;
            } while (uVar6 < uVar4);
          }
          uVar5 = uVar5 + 1;
        } while (uVar5 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1068));
      }
      OID__FreeObject_Callback(ptr);
      return 0;
    }
  }
  return -0x7fffbffb;
}
