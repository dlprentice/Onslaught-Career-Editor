/* address: 0x00567338 */
/* name: CTexture__Helper_00567338 */
/* signature: int __cdecl CTexture__Helper_00567338(void * param_1, uint param_2, uint param_3) */


int __cdecl CTexture__Helper_00567338(void *param_1,uint param_2,uint param_3)

{
  byte *pbVar1;
  byte *pbVar2;
  byte bVar3;
  byte *pbVar4;
  uint uVar5;
  byte *pbVar6;

  pbVar2 = *(byte **)param_1;
  pbVar1 = (byte *)((int)param_1 + 0xf8);
  bVar3 = (byte)param_3;
  if (*(uint *)((int)param_1 + 4) < param_3) {
    pbVar6 = pbVar2;
    if (pbVar2[*(uint *)((int)param_1 + 4)] != 0) {
      pbVar6 = pbVar2 + *(uint *)((int)param_1 + 4);
    }
    while( true ) {
      while( true ) {
        if (pbVar1 <= pbVar6 + param_3) {
          pbVar6 = (byte *)((int)param_1 + 8);
          while( true ) {
            while( true ) {
              if (pbVar2 <= pbVar6) {
                return 0;
              }
              if (pbVar1 <= pbVar6 + param_3) {
                return 0;
              }
              if (*pbVar6 == 0) break;
              pbVar6 = pbVar6 + *pbVar6;
            }
            uVar5 = 1;
            pbVar4 = pbVar6;
            while (pbVar4 = pbVar4 + 1, *pbVar4 == 0) {
              uVar5 = uVar5 + 1;
            }
            if (param_3 <= uVar5) break;
            param_2 = param_2 - uVar5;
            pbVar6 = pbVar4;
            if (param_2 < param_3) {
              return 0;
            }
          }
          if (pbVar6 + param_3 < pbVar1) {
            *(byte **)param_1 = pbVar6 + param_3;
            *(uint *)((int)param_1 + 4) = uVar5 - param_3;
          }
          else {
            *(undefined4 *)((int)param_1 + 4) = 0;
            *(int *)param_1 = (int)param_1 + 8;
          }
          *pbVar6 = bVar3;
          pbVar2 = pbVar6 + 8;
          goto LAB_0056744b;
        }
        if (*pbVar6 == 0) break;
        pbVar6 = pbVar6 + *pbVar6;
      }
      uVar5 = 1;
      pbVar4 = pbVar6;
      while (pbVar4 = pbVar4 + 1, *pbVar4 == 0) {
        uVar5 = uVar5 + 1;
      }
      if (param_3 <= uVar5) break;
      if (pbVar6 == pbVar2) {
        *(uint *)((int)param_1 + 4) = uVar5;
        pbVar6 = pbVar4;
      }
      else {
        param_2 = param_2 - uVar5;
        pbVar6 = pbVar4;
        if (param_2 < param_3) {
          return 0;
        }
      }
    }
    if (pbVar6 + param_3 < pbVar1) {
      *(byte **)param_1 = pbVar6 + param_3;
      *(uint *)((int)param_1 + 4) = uVar5 - param_3;
    }
    else {
      *(undefined4 *)((int)param_1 + 4) = 0;
      *(int *)param_1 = (int)param_1 + 8;
    }
    *pbVar6 = bVar3;
    pbVar2 = pbVar6 + 8;
  }
  else {
    *pbVar2 = bVar3;
    if (pbVar2 + param_3 < pbVar1) {
      *(uint *)param_1 = *(int *)param_1 + param_3;
      *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) - param_3;
    }
    else {
      *(undefined4 *)((int)param_1 + 4) = 0;
      *(int *)param_1 = (int)param_1 + 8;
    }
    pbVar2 = pbVar2 + 8;
  }
LAB_0056744b:
  return (int)pbVar2 * 0x10 + (int)param_1 * -0xf;
}
