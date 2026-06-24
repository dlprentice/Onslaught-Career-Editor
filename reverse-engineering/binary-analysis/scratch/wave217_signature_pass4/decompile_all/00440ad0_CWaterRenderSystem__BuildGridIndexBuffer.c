/* address: 0x00440ad0 */
/* name: CWaterRenderSystem__BuildGridIndexBuffer */
/* signature: void __stdcall CWaterRenderSystem__BuildGridIndexBuffer(void * out_indices, int grid_width, int grid_height, int flip_winding) */


void CWaterRenderSystem__BuildGridIndexBuffer
               (void *out_indices,int grid_width,int grid_height,int flip_winding)

{
  undefined2 uVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  short *psVar5;
  int iVar6;
  short sVar7;
  int iVar8;
  int iVar9;
  int local_4;

  iVar4 = grid_width;
  iVar8 = grid_width + 1;
  if (0 < grid_height) {
    grid_width = 0;
    local_4 = grid_height;
    psVar5 = out_indices;
    do {
      iVar6 = grid_width;
      iVar9 = iVar4;
      if (0 < iVar4) {
        do {
          sVar2 = (short)iVar6;
          sVar3 = (short)iVar8;
          sVar7 = sVar2 + 1 + sVar3;
          psVar5[1] = sVar2 + sVar3;
          *psVar5 = sVar2;
          psVar5[2] = sVar7;
          psVar5[3] = sVar2;
          psVar5[5] = sVar2 + 1;
          psVar5[4] = sVar7;
          psVar5 = psVar5 + 6;
          iVar9 = iVar9 + -1;
          iVar6 = iVar6 + 1;
        } while (iVar9 != 0);
      }
      grid_width = grid_width + iVar8;
      local_4 = local_4 + -1;
    } while (local_4 != 0);
  }
  if (flip_winding != 0) {
    for (iVar8 = iVar4 * grid_height * 2; iVar8 != 0; iVar8 = iVar8 + -1) {
      uVar1 = *(undefined2 *)out_indices;
      *(undefined2 *)out_indices = *(undefined2 *)((int)out_indices + 2);
      *(undefined2 *)((int)out_indices + 2) = uVar1;
      out_indices = (void *)((int)out_indices + 6);
    }
  }
  return;
}
