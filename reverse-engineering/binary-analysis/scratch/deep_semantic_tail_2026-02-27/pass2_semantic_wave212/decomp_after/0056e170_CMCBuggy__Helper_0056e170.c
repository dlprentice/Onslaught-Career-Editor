/* address: 0x0056e170 */
/* name: CMCBuggy__Helper_0056e170 */
/* signature: int __cdecl CMCBuggy__Helper_0056e170(void * param_1, void * param_2, void * param_3) */


int __cdecl CMCBuggy__Helper_0056e170(void *param_1,void *param_2,void *param_3)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  ushort uVar4;
  uint uVar5;
  void *pvVar6;
  int iVar7;
  void *this;
  void *pvVar8;
  bool bVar9;

  iVar2 = DAT_009d35f0;
  iVar7 = 0;
  if (param_3 != (void *)0x0) {
    if (DAT_009d0998 == 0) {
      do {
        bVar3 = *(byte *)param_1;
        cVar1 = *(char *)param_2;
        uVar4 = CONCAT11(bVar3,cVar1);
        if (bVar3 == 0) break;
        uVar4 = CONCAT11(bVar3,cVar1);
        uVar5 = (uint)uVar4;
        if (cVar1 == '\0') break;
        param_1 = (void *)((int)param_1 + 1);
        param_2 = (void *)((int)param_2 + 1);
        if ((0x40 < bVar3) && (bVar3 < 0x5b)) {
          uVar5 = (uint)CONCAT11(bVar3 + 0x20,cVar1);
        }
        uVar4 = (ushort)uVar5;
        bVar3 = (byte)uVar5;
        if ((0x40 < bVar3) && (bVar3 < 0x5b)) {
          uVar4 = (ushort)CONCAT31((int3)(uVar5 >> 8),bVar3 + 0x20);
        }
        bVar3 = (byte)(uVar4 >> 8);
        bVar9 = bVar3 < (byte)uVar4;
        if (bVar3 != (byte)uVar4) goto LAB_0056e1cf;
        param_3 = (void *)((int)param_3 + -1);
      } while (param_3 != (void *)0x0);
      iVar7 = 0;
      bVar3 = (byte)(uVar4 >> 8);
      bVar9 = bVar3 < (byte)uVar4;
      if (bVar3 != (byte)uVar4) {
LAB_0056e1cf:
        iVar7 = -1;
        if (!bVar9) {
          iVar7 = 1;
        }
      }
    }
    else {
      LOCK();
      DAT_009d35f0 = DAT_009d35f0 + 1;
      UNLOCK();
      bVar9 = 0 < DAT_009d35ec;
      if (bVar9) {
        LOCK();
        UNLOCK();
        DAT_009d35f0 = iVar2;
        CRT__LockByIndex(0x13);
      }
      uVar5 = (uint)bVar9;
      pvVar6 = (void *)0x0;
      pvVar8 = (void *)0x0;
      do {
        pvVar6 = (void *)CONCAT31((int3)((uint)pvVar6 >> 8),*(undefined1 *)param_1);
        pvVar8 = (void *)CONCAT31((int3)((uint)pvVar8 >> 8),*(undefined1 *)param_2);
        if ((pvVar6 == (void *)0x0) || (pvVar8 == (void *)0x0)) break;
        param_1 = (void *)((int)param_1 + 1);
        param_2 = (void *)((int)param_2 + 1);
        pvVar8 = (void *)CMCBuggy__Helper_0056961e(param_3,pvVar8,(uint)pvVar6);
        pvVar6 = (void *)CMCBuggy__Helper_0056961e(this,pvVar6,(uint)param_3);
        bVar9 = pvVar6 < pvVar8;
        if (pvVar6 != pvVar8) goto LAB_0056e245;
        param_3 = (void *)((int)param_3 + -1);
      } while (param_3 != (void *)0x0);
      iVar7 = 0;
      bVar9 = pvVar6 < pvVar8;
      if (pvVar6 != pvVar8) {
LAB_0056e245:
        iVar7 = -1;
        if (!bVar9) {
          iVar7 = 1;
        }
      }
      if (uVar5 == 0) {
        LOCK();
        DAT_009d35f0 = DAT_009d35f0 + -1;
        UNLOCK();
      }
      else {
        CRT__UnlockByIndex(0x13);
      }
    }
  }
  return iVar7;
}
