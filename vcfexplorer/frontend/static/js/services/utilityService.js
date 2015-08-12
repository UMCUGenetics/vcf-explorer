angular
  .module('vcfExplorerApp')
  .factory('utilityService', utilityService);

  function utilityService(){
    return {
      getUploadDate: getUploadDate
    };
  };

  // Valuegetter for upload date
  function getUploadDate(params) {
    return new Date(params.data.upload_date.$date);
  };
