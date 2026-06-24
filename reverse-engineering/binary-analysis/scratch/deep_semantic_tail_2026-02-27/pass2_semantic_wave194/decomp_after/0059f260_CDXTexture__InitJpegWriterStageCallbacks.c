/* address: 0x0059f260 */
/* name: CDXTexture__InitJpegWriterStageCallbacks */
/* signature: void __stdcall CDXTexture__InitJpegWriterStageCallbacks(int param_1) */


void CDXTexture__InitJpegWriterStageCallbacks(int param_1)

{
  undefined4 *puVar1;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x20);
  *(undefined4 **)(param_1 + 0x164) = puVar1;
  *puVar1 = CDXTexture__WriteJpegStartOfImageAndMetadata;
  puVar1[1] = CDXTexture__WriteJpegQuantTablesAndFrame;
  puVar1[2] = CDXTexture__WriteJpegHuffmanAndScanHeaders;
  puVar1[3] = CDXTexture__WriteJpegEndOfImage;
  puVar1[4] = &LAB_0059f170;
  puVar1[5] = CDXTexture__WriteJpegSegmentMarkerAndLength;
  puVar1[6] = &LAB_0059eea0;
  puVar1[7] = 0;
  return;
}
