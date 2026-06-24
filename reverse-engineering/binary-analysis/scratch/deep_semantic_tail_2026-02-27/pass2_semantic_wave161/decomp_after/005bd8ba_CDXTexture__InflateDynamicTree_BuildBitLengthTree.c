/* address: 0x005bd8ba */
/* name: CDXTexture__InflateDynamicTree_BuildBitLengthTree */
/* signature: int __stdcall CDXTexture__InflateDynamicTree_BuildBitLengthTree(int param_1, void * param_2, int param_3, int param_4, int param_5) */


int CDXTexture__InflateDynamicTree_BuildBitLengthTree
              (int param_1,void *param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;

  iVar1 = (**(code **)(param_5 + 0x20))(*(undefined4 *)(param_5 + 0x28),0x13,4);
  if (iVar1 == 0) {
    iVar2 = -4;
  }
  else {
    iVar2 = CDXTexture__BuildInflateHuffmanTable();
    if (iVar2 == -3) {
      *(char **)(param_5 + 0x18) = "oversubscribed dynamic bit lengths tree";
    }
    else if ((iVar2 == -5) || (*(int *)param_2 == 0)) {
      *(char **)(param_5 + 0x18) = "incomplete dynamic bit lengths tree";
      iVar2 = -3;
    }
    (**(code **)(param_5 + 0x24))(*(undefined4 *)(param_5 + 0x28),iVar1);
  }
  return iVar2;
}
