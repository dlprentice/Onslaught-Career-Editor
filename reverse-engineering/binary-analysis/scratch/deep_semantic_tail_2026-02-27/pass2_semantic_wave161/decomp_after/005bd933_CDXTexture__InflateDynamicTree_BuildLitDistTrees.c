/* address: 0x005bd933 */
/* name: CDXTexture__InflateDynamicTree_BuildLitDistTrees */
/* signature: int __stdcall CDXTexture__InflateDynamicTree_BuildLitDistTrees(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


int CDXTexture__InflateDynamicTree_BuildLitDistTrees
              (void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  int iVar1;
  int iVar2;
  int in_stack_00000024;

  iVar1 = (**(code **)(in_stack_00000024 + 0x20))(*(undefined4 *)(in_stack_00000024 + 0x28),0x120,4)
  ;
  if (iVar1 == 0) {
    return -4;
  }
  iVar2 = CDXTexture__BuildInflateHuffmanTable();
  if (iVar2 == 0) {
    if (*(int *)param_4 == 0) goto LAB_005bda0f;
    iVar2 = CDXTexture__BuildInflateHuffmanTable();
    if (iVar2 == 0) {
      if ((*(int *)param_5 != 0) || (param_1 < (void *)0x102)) {
        iVar2 = 0;
        goto LAB_005bda1b;
      }
LAB_005bd9f3:
      *(char **)(in_stack_00000024 + 0x18) = "empty distance tree with lengths";
    }
    else {
      if (iVar2 == -3) {
        *(char **)(in_stack_00000024 + 0x18) = "oversubscribed distance tree";
        goto LAB_005bda1b;
      }
      if (iVar2 != -5) {
        if (iVar2 == -4) goto LAB_005bda1b;
        goto LAB_005bd9f3;
      }
      *(char **)(in_stack_00000024 + 0x18) = "incomplete distance tree";
    }
  }
  else {
    if (iVar2 == -3) {
      *(char **)(in_stack_00000024 + 0x18) = "oversubscribed literal/length tree";
      goto LAB_005bda1b;
    }
    if (iVar2 == -4) goto LAB_005bda1b;
LAB_005bda0f:
    *(char **)(in_stack_00000024 + 0x18) = "incomplete literal/length tree";
  }
  iVar2 = -3;
LAB_005bda1b:
  (**(code **)(in_stack_00000024 + 0x24))(*(undefined4 *)(in_stack_00000024 + 0x28),iVar1);
  return iVar2;
}
